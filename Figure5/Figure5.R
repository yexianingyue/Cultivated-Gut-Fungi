### Global
library(dplyr)
library(reshape2)
library(ggrepel)
library(ggplot2)

### Figure 5a
rm(list=ls())
load("./fig5a.RData")
fig5a <- fig5a1 + theme(legend.position="none",axis.title.x=element_blank()) +
    fig5a2 + remove_y + theme(legend.position = "bottom") +
    fig5a3 + remove_y + theme(legend.position="none")

ggsave("fig5a.pdf", fig5a, width=20, height=8)


### Figure 5b
rm(list=ls())
load("./fig5b.RData")
xlab = paste("CAP1", " (", eigs[1], "% )", sep="")
ylab = paste("CAP3", " (", eigs[2], "% )", sep="")

x_min = min(data$CAP1)
x_max = max(data$CAP1)
y_min = min(data$CAP2)
y_max = max(data$CAP2)

p <- ggplot(data,aes(x=CAP1, y=CAP2, color=group))+
    geom_point()+
    geom_text_repel(aes(label=`Row.names`))+
    xlim(x_min, x_max)+
    ylim(y_min, y_max)+
    theme_bw()+
    theme(legend.position = 'none')+
    xlab(label=xlab)+ ylab(label=ylab)+
    scale_color_manual(values=colors.project)

use_pro = c("cardiometabolic disease","cancer","digestive disease","immune disease")
yplot <-
    data %>%
    filter(group %in% use_pro) %>%
    ggplot(.,aes(y=CAP2,x=group, fill=group))+
    geom_boxplot()+
    theme_bw()+
    theme(axis.title.y = element_blank(),
          axis.text.x = element_text(angle=90),
          legend.position = "none")+
    geom_signif(comparisons =combn(use_pro,2,list),test='wilcox.test',step_increase = 0.1)+
    #ylim(y_min, y_max)+
    scale_fill_manual(values=colors.project)

xplot <-
    data %>%
    filter(group %in% use_pro) %>%
    ggplot(.,aes(x=CAP1,y=group, fill=group))+
    geom_boxplot() +
    geom_signif(comparisons =combn(use_pro,2,list),test='wilcox.test',step_increase = 0.1)+
    theme_bw()+
    theme(axis.title.x = element_blank(),
          legend.position = "none")+
    scale_fill_manual(values=colors.project)

fig5b <- xplot+ggplot()+
    p+yplot+
    plot_layout(ncol=2,nrow=2,
                widths=c(4,1),
                heights=c(1,4))
ggsave("fig5b.pdf",fig5b, width=15, hieght=15)


### Figure 5c-e
rm(list=ls())
load("fig5c-e.RData")

pdf("fig5c.pdf", width=12, height=22)
get_heatmap(proj_map, dtf, samp)
dev.off()

pdf("fig5d.pdf", width=12, height=22)
get_heatmap(proj_map, dtg, samp)
dev.off()

pdf("fig5e.pdf", width=12, height=22)
get_heatmap(proj_map, dts, samp)
dev.off()
