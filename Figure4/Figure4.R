library(ggplot2)

### Figure 4a
rm(list=ls())
load("fig4a.RData") # load data
fig4a <- ggplot(data=fig4a_data, aes(x=depth, y=rho, color=depth))+
    geom_boxplot()+
    geom_jitter(width=0.1)+
    facet_grid(.~Project, scales="free_y")

ggsave("fig4a.pdf", fig4a, width=8, height=4.5)

### Figure 4b-c
rm(list=ls())
load("./fig4b-c.RData")
cgf_p <- ggplot(data=cgfl, aes(x=log10(value+0.01)))+
    theme_bw()+
    geom_histogram(binwidth=0.1, boundary=0, position='stack', color="black", fill="#66c2a5")+
    facet_wrap(variable~., scales='free', ncol=1)+
    scale_fill_brewer(palette = 'Set1')+
    theme(panel.grid=element_blank())+
    scale_y_continuous(breaks = scales::pretty_breaks(), limits = c(0,15))+
    scale_x_continuous(breaks = c(-2,-1,0,1,2),limits =c(-2,2),
                       label = c("≤0.01","0.1","1","10","100"))+
    xlab(label="%Prevalence rate")+
    ylab("Number of species")+
    geom_vline(xintercept = log10(c(1,10)), linetype="dashed", color="red")

phf_p <- ggplot(data=phfl, aes(x=log10(value+0.01), fill=Site))+
    theme_bw()+
    geom_histogram(binwidth=0.1, boundary=0, position='stack', color='black')+
    facet_wrap(variable~., scales='free', ncol=1)+
    scale_fill_brewer(palette = 'Set1')+
    theme(panel.grid=element_blank())+
    scale_fill_manual(values=structure(c("#fc8d62","#8da0cb"), names=c("Other","Respiratory/digestive tract")))+
    scale_y_continuous(breaks = scales::pretty_breaks(), limits = c(0,15))+
    scale_x_continuous(breaks = c(-2,-1,0,1,2),limits =c(-2,2),
                       label = c("≤0.01","0.1","1","10","100"))+
    xlab(label="%Prevalence rate")+
    ylab("Number of species")+
    geom_vline(xintercept = log10(c(1,10)), linetype="dashed", color="red")

fig4bc <- cgf_p + phf_p
ggsave("fig4b-c.pdf",fig4bc, width=12, height=7)



### Figure 4d-e
rm(list=ls())
load("./fig4d-e.RData")

fig4d <- ggplot(fig4d_data, aes(x=Var2, y=value, fill=Var1))+
    geom_bar(stat='identity',width=0.9)+
    theme_bw()+
    theme(panel.grid = element_blank(),
          strip.placement = "outside",
          axis.text.x = element_text(angle=90, hjust=1))+
    facet_grid( .~ Site, scale='free',space = 'free_x'
                ,switch = "both" # 标签在下
    )+
    labs(title="Composition at subPhylum/Phylum level")+
    scale_fill_manual(values=taxo.color)+
    scale_y_continuous(expand = c(0,0))

fig4e <- ggplot(fig4e_data, aes(x=Var2, y=value, fill=Var1))+
    geom_bar(stat='identity',width=0.9)+
    theme_bw()+
    theme(panel.grid = element_blank(),
          strip.placement = "outside",
          axis.text.x = element_text(angle=90, hjust=1))+
    facet_grid( .~ Site, scale='free',space = 'free_x'
                ,switch = "both" # 标签在下
    )+
    labs(title="Composition at Species level")+
    scale_fill_manual(values=taxo.color)+
    scale_y_continuous(expand = c(0,0))
figde <- fig4d + fig4e
ggsave("fig4d-e.pdf", figde, width=25, height=8)

